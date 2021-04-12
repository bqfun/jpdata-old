package main

import (
	"encoding/csv"
	"fmt"
	"golang.org/x/text/encoding/japanese"
	"golang.org/x/text/transform"
	"net/http"
	"os"
	"path"
	"regexp"
	"strconv"
	"strings"
	"time"
)

func main() {
	// https://www.hokoukukan.go.jp/metadata/detail/23
	destination := os.Getenv("DESTINATION")
	err := os.MkdirAll(destination, 0777)
	if err != nil {
		panic(err)
	}
	url := "https://www.hokoukukan.go.jp/download/mlit_housing_nintei.csv"
	name := path.Join(destination, "accessible_buildings.csv")
	records, err := readShiftJisCsvFromUrl(url)
	if err != nil {
		panic(err)
	}

	refined := [][]string{{
		"prefecture",
		"address",
		"name",
		"use",
		"number_of_floors__above_ground",
		"number_of_floors__underground",
		"number_of_elevators",
		"gross_floor_area",
		"date_nintei__year",
		"date_nintei__month",
		"date_nintei__day",
		"latitude",
		"longitude",
	}}
	re1 := regexp.MustCompile(`\n(・|及び)`)
	re2 := regexp.MustCompile(`(等|総合|･)\n`)

	for _, row := range records[1:] {
		year, month, day, err := parseDate(row[9])
		if err != nil {
			panic(err)
		}
		r := []string{
			row[1],
			strings.TrimSpace(row[2]),
			strings.TrimSpace(row[3]),
			strings.ReplaceAll(re2.ReplaceAllString(re1.ReplaceAllString(row[4], `$1`), `$1`), "\n", "，"),
			row[5],
			map[bool]string{true: "", false: row[6]}[row[6] == "-"],
			map[bool]string{true: "", false: row[7]}[row[7] == "-"],
			map[bool]string{true: "", false: row[8]}[row[8] == "-"],
			year,
			month,
			day,
			map[bool]string{true: "", false: row[10]}[row[10] == "-"],
			map[bool]string{true: "", false: row[11]}[row[11] == "-"],
		}
		refined = append(refined, r)
	}

	if err := writeCsvToFile(name, refined); err != nil {
		panic(err)
	}
}

// optional intみたいな振る舞いできない？
func parseDate(value string) (string, string, string, error) {
	if value == "-" {
		return "", "", "", nil
	}
	if value == "20130700" {
		return "2013", "7", "", nil
	}
	// パターンを外部から受け取るならCompileで、内部で定義してるから
	// MustCompileでエラーハンドリング省略してもいい？
	re := regexp.MustCompile(`(199[4-9]|200[0-9]|201[0-2])0000`)
	m := re.FindStringSubmatch(value)
	if len(m) == 2 {
		return m[1], "", "", nil
	}
	date, err := time.Parse("20060102", value)
	if err != nil {
		return "", "", "", err
	}
	year, month, day := date.Date()
	return strconv.Itoa(year), strconv.Itoa(int(month)), strconv.Itoa(day), nil
}

func writeCsvToFile(name string, records [][]string) error {
	file, err := os.Create(name)
	if err != nil {
		return err
	}
	defer func() {
		cerr := file.Close()
		if cerr != nil {
			err = fmt.Errorf("Failed to close: %v, the original error was %v", cerr, err)
		}
	}()

	writer := csv.NewWriter(file)
	return writer.WriteAll(records)
}

func readShiftJisCsvFromUrl(url string) ([][]string, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}

	defer func() {
		cerr := resp.Body.Close()
		if cerr != nil {
			panic(cerr)
		}
		err = fmt.Errorf("Failed to close: %v, the original error was %v", cerr, err)
	}()
	transformer := japanese.ShiftJIS.NewDecoder()
	reader := csv.NewReader(transform.NewReader(resp.Body, transformer))
	return reader.ReadAll()
}
