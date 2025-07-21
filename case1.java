public class FileReaderExample {
    public static void main(String[] args) {
        FileReader fr = new FileReader("config.txt");
        BufferedReader br = new BufferedReader(fr);
        String line = br.readLine();
        System.out.println("First line: " + line);
        br.close();
    }
}
