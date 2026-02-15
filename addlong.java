import java.util.Scanner;
class addlong {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        long a, b;
        System.out.println("enter a:");
        a = in.nextLong();
        System.out.println("enter b:");
        b = in.nextLong();
        System.out.println(a + b);
    }
}