import csv
import glob
import os
import re
import shutil
import urllib.parse
import urllib.request
import zipfile


def download(file: str) -> None:
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0"

    url = "https://www.houjin-bangou.nta.go.jp/download/zenken/"
    headers = {"User-Agent": user_agent}

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        body = response.read()

    token = re.search(b'value="([a-z0-9-]{36})"', body).group(1).decode()

    data = {
        "jp.go.nta.houjin_bangou.framework.web.common.CNSFWTokenProcessor.request.token": token,
        "selDlFileNo": 13373,
        "event": "download",
    }
    headers = {"User-Agent": user_agent}

    req = urllib.request.Request(
        "https://www.houjin-bangou.nta.go.jp/download/zenken/index.html",
        urllib.parse.urlencode(data).encode("ascii"),
        headers=headers,
    )

    with urllib.request.urlopen(req) as res, open(file, "wb") as f:
        shutil.copyfileobj(res, f)


def unzip(file):
    with zipfile.ZipFile(file) as f:
        f.extractall()


def _process(process: str) -> str:
    if process == "01":
        return "新規"
    if process == "11":
        return "商号又は名称の変更"
    if process == "12":
        return "国内所在地の変更"
    if process == "13":
        return "国外所在地の変更"
    if process == "21":
        return "登記記録の閉鎖等"
    if process == "22":
        return "登記記録の復活等"
    if process == "71":
        return "吸収合併"
    if process == "72":
        return "吸収合併無効"
    if process == "81":
        return "商号の登記の抹消"
    if process == "99":
        return "削除"


def _correct(correct: str) -> str:
    if correct == "0":
        return "訂正以外"
    if correct == "1":
        return "訂正"
    raise ValueError


def _kind(kind: str) -> str:
    if kind == "101":
        return "国の機関"
    if kind == "201":
        return "地方公共団体"
    if kind == "301":
        return "株式会社"
    if kind == "302":
        return "有限会社"
    if kind == "303":
        return "合名会社"
    if kind == "304":
        return "合資会社"
    if kind == "305":
        return "合同会社"
    if kind == "399":
        return "その他の設立登記法人"
    if kind == "401":
        return "外国会社等"
    if kind == "499":
        return "その他"
    raise ValueError


# def _latest(latest: str) -> str:
#     if latest == "0":
#         return "過去情報"
#     if latest == "1":
#         return "最新情報"
#     raise ValueError


def _hihyoji(hihyoji: str) -> str:
    if hihyoji == "0":
        return "検索対象"
    if hihyoji == "1":
        return "検索対象除外"
    raise ValueError


def clean(source: str, destination: str):

    with open(source) as s, open(destination, "w") as d:
        reader = csv.reader(s)
        writer = csv.writer(d)

        writer.writerow(
            (
                "sequence_number",
                "corporate_number",
                "process",
                "correct",
                "update_date",
                "change_date",
                "name",
                "name_image_id",
                "kind",
                "prefecture_name",
                "city_name",
                "street_number",
                "address_image_id",
                "prefecture_code",
                "city_code",
                "post_code",
                "address_outside",
                "address_outside_image_id",
                "close_date",
                "close_cause",
                "successor_corporate_number",
                "change_cause",
                "assignment_date",
                # "latest",  # 必ず1が入るので除外
                "en_name",
                "en_prefecture_name",
                "en_city_name",
                "en_address_outside",
                "furigana",
                "hihyoji",
            )
        )
        writer.writerows(
            (
                # sequence_number
                row[0],
                # corporate_number
                row[1],
                # process
                _process(row[2]),
                # correct
                _correct(row[3]),
                # update_date
                row[4],
                # change_date
                row[5],
                # name
                row[6],
                # name_image_id
                row[7],
                # kind
                _kind(row[8]),
                # prefecture_name
                row[9],
                # city_name
                row[10],
                # street_number
                row[11],
                # address_image_id
                row[12],
                # prefecture_code
                row[13],
                # city_code
                row[14],
                # post_code
                row[15],
                # address_outside
                row[16],
                # address_outside_image_id
                row[17],
                # close_date
                row[18],
                # close_cause
                row[19],
                # successor_corporate_number
                row[20],
                # change_cause
                row[21],
                # assignment_date
                row[22],
                # latest
                # _latest(row[23]),  # 必ず1が入るので除外
                # en_name
                row[24],
                # en_prefecture_name
                row[25],
                # en_city_name
                row[26],
                # en_address_outside
                row[27],
                # furigana
                row[28],
                # hihyoji
                _hihyoji(row[29]),
            )
            for row in reader
        )


def main():
    destination = os.environ["DESTINATION"]
    os.makedirs(destination, exist_ok=True)
    download("corporate_numbers.zip")
    unzip("corporate_numbers.zip")
    file = next(glob.iglob("00_zenkoku_all_*.csv"))
    clean(file, os.path.join(destination, "corporate_numbers.csv"))


if __name__ == "__main__":
    main()
