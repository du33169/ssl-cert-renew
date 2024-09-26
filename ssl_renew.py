from tencent_api import TencentApi
import json 
import os

# secret=json.load(open('secret.json'))
def main(a,b): # dump args, for cloud function entry
    tc=TencentApi(
        secret_id = os.getenv("SECRET_ID"),
        secret_key = os.getenv("SECRET_KEY"),
        token = "",
        service = "ssl",
        host = "ssl.tencentcloudapi.com",
        region = "",
        version = "2019-12-05"
    )

    # query cert list
    res=tc.send(
        action = "DescribeCertificates",
        params =  {
            "Limit": 1000,
            "CertificateStatus": [1],
            "FilterExpiring": 1
        }
    )
    # with open("certs.json", "w") as f:
    # 	json.dump(res, f, indent=4)

    RenewCertDict={r["CertificateId"]:r for r in res["Response"]["Certificates"]}
    print("Expiring CertId List:",list(RenewCertDict.keys()))


    for certId,certInfo in RenewCertDict.items():
        domain=certInfo["Domain"]
        if certInfo["RenewAble"]==True:
            print(certId, "RenewAble:",certInfo["RenewAble"], "requesting new cert...")
            # request new cert
            res=tc.send(
                action="ApplyCertificate",
                params={
                    "DvAuthMethod": "DNS_AUTO",
                    "DomainName": domain,
                    "OldCertificateId": certId,
                    "DeleteDnsAutoRecord": True
                }
            )
            newId=res["Response"]["CertificateId"]
            print(f"New certId {newId} for {domain} requested.")
        
        if certInfo["HasRenewOrder"]!="" and certInfo["HasRenewOrder"]!=None:
            newId=certInfo["HasRenewOrder"]
            print(certId, "Has Renew Order:",newId, "updating cert...")
            # update resources
            res=tc.send(
                action="UpdateCertificateInstance",
                params={
                    "OldCertificateId": certId,
                    "CertificateId": newId,
                    "ResourceTypes":["cdn"]
                }
            )
            print(json.dumps(res["Response"], indent=4, ensure_ascii=False))
            print(f"update domain {domain} from cert {certId} to {newId}", "success" if int(res["Response"]["DeployStatus"])==1 else "failed")

    # remove expired/cancelled/revoked cert
    removeList=[]
    statusMap={
        3: "expired",
        7: "cancelled",
        10: "revoked"
    }
    for status,desc in statusMap.items(): # expired, cancelled, revoked
        res=tc.send(
            action = "DescribeCertificates",
            params =  {
                "Limit": 1000,
                "CertificateStatus": [status], 
            }
        )
        RenewCertDict={r["CertificateId"]:r for r in res["Response"]["Certificates"]}
        curList=[r["CertificateId"] for r in RenewCertDict.values()]
        removeList.extend(curList)
        print(f"{desc} CertId List:",curList)
    if len(removeList)>0:
        print("deleting expired, cancelled, revoked CertId List:",removeList)

        res=tc.send(
            action = "DeleteCertificates",
            params =  {
                "CertificateIds":removeList
            }
        )
        print(json.dumps(res["Response"], indent=4, ensure_ascii=False))
    else:
        print("All certs clear.")

if __name__ == "__main__":
    main(0,0)