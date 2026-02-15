import java.util.Scanner;
class Ssum {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        int n, a = 0;
        int i;

        System.out.println("Enter number:");
        n = in.nextInt();

        for (i = 1; i <= n; i++) {
            a = a + i;
        }

        System.out.println("Sum: " + a);
    }
}
