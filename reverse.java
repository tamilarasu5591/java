import java.util.Scanner;
class Reverse {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        int i, n;

        System.out.println("Enter number:");
        n = in.nextInt();

        for (i = n; i >= 1; i--) {
            System.out.println(i);
        }
    }
}
