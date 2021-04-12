import java.io.*;
import java.net.URL;
import java.util.Arrays;
import java.util.Objects;
import java.util.stream.IntStream;

public class Main {
  public static void main(String[] args) throws IOException {
    final String destination = System.getenv("DESTINATION");
    Objects.requireNonNull(destination, "DESTINATION environment variable is required");
    new File(destination).mkdirs();

    // https://www5.cao.go.jp/keizai-shimon/kaigi/special/future/keizai-jinkou_data.html
    final URL url =
        new URL(
            "https://www5.cao.go.jp/keizai-shimon/kaigi/special/future/keizai-jinkou_data/csv/file02.csv");

    // 市区町村名,市区町村コード,1970年,1975年,...
    // 北海道 札幌市,11002,20265,23404
    // 北海道 函館市,12025,5621,5627
    final String[][] numberOfBirths;
    try (final BufferedReader reader =
        new BufferedReader(new InputStreamReader(url.openStream(), "Shift-JIS"))) {
      numberOfBirths = reader.lines().skip(7).map(line -> line.split(",")).toArray(String[][]::new);
    }

    // 市区町村名,市区町村コード,1970年,1975年,...
    final String[] header = numberOfBirths[0];
    // 1970,1975,...
    final String[] years =
        Arrays.stream(header)
            .skip(2)
            .map(it -> it.substring(0, it.length() - 1))
            .toArray(String[]::new);

    // 北海道 札幌市,11002,1970,20265
    // 北海道 札幌市,11002,1975,23404
    // 北海道 札幌市,11002,1975,22251
    final String[][] csv =
        Arrays.stream(numberOfBirths)
            .skip(2)
            .flatMap(
                row ->
                    IntStream.range(0, years.length)
                        .mapToObj(i -> new String[] {row[0], row[1], years[i], row[2 + i]}))
            .filter(row -> !"".equals(row[3]))
            .filter(row -> !"－".equals(row[3]))
            .toArray(String[][]::new);

    try (final FileWriter writer = new FileWriter(new File(destination, "number_of_births.csv"))) {
      writer.write("city,city_code,year,number_of_births\r\n");
      for (final String[] row : csv) {
        writer.write(String.join(",", row));
        writer.write("\r\n");
      }
    }
  }
}
