# HTTPS化で必要な、コンソール管理リソースの識別子。
# 下記2つはAWSコンソールで確認して書き換えること:
# - certificate_arn: ACM > 証明書 > turbofan-api.parabolaorbit-dev.net のARN
# - hosted_zone_id : Route53 > ホストゾーン > parabolaorbit-dev.net のゾーンID(Z...)
certificate_arn = "arn:aws:acm:ap-northeast-1:097853039113:certificate/a30332b7-28d1-45b9-946e-571f22a76532"
hosted_zone_id  = "Z060775834GS2YFH9UGUC"
