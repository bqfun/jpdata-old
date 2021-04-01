import csv
import glob
import os
import re
import shutil
import tempfile
import unicodedata
import urllib.request
import zipfile

from openpyxl import load_workbook


def fetch_latest_file_url():
    with urllib.request.urlopen(
        "https://www.pmda.go.jp/review-services/drug-reviews/foreign-mfr/0003.html"
    ) as res:
        body = res.read()

    # 最新のファイル名を特定
    m = re.search(b"/files/\\d{9}.zip", body)
    if not m:
        raise Exception
    return f"https://www.pmda.go.jp/{m.group().decode()}"


def download_file(url: str, file: str):
    with urllib.request.urlopen(url) as source, open(
        file, "wb"
    ) as destination:
        shutil.copyfileobj(source, destination)


def unzip(file: str):
    with zipfile.ZipFile(file) as z:
        for info in z.infolist():
            info.filename = info.filename.encode("cp437").decode("cp932")
            z.extract(info, path=os.path.dirname(file))


def find_file(file):
    return glob.glob(file)[0]


def extract_csv(xlsx_file: str, file: str):
    workbook = load_workbook(filename=xlsx_file, read_only=True)
    worksheet = workbook["外国製造業者認定・登録一覧"]

    rows = worksheet.rows
    # remove headers
    next(rows)
    next(rows)
    next(rows)

    with open(file, "w") as f:
        c = csv.writer(f)
        c.writerow(
            (
                "applicant_code__corporation",
                "applicant_code__office",
                "registration_number",
                "type_of_business",
                "type_of_registration",
                "name",
                "address",
                "date_of_registration",
                "expiry_date",
                "date_of_abolishment",
                "application_for_re_registration_submitted",
                "country",
            )
        )
        c.writerows(
            (
                row[0].value,
                row[1].value,
                row[2].value,
                row[3].value,
                row[4].value,
                unicodedata.normalize("NFKC", row[5].value),
                unicodedata.normalize("NFKC", row[7].value),
                row[9].value.date(),
                row[10].value.date(),
                None if row[11].value is None else row[11].value.date(),
                row[12].value == "○",
                row[14].value,
            )
            for row in rows
        )


def main():
    destination = os.environ["DESTINATION"]
    url = fetch_latest_file_url()
    os.makedirs(destination, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdirname:
        download_file(
            url,
            os.path.join(tmpdirname, "accredited_foreign_manufacturers.zip"),
        )
        unzip(os.path.join(tmpdirname, "accredited_foreign_manufacturers.zip"))
        xlsx_file = find_file(
            os.path.join(tmpdirname, "外国製造業者認定・登録リスト_*.xlsx")
        )
        extract_csv(
            xlsx_file,
            os.path.join(destination, "accredited_foreign_manufacturers.csv"),
        )


if __name__ == "__main__":
    main()
