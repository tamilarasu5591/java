import java.util.Scanner;
class hex{
        public static void main(String[] args){
            Scanner in = new Scanner(System.in);
            int binary n;
            System.out.println("enter number:");
            n=in.nextInt();
            System.out.println(Integer.toHexString(n));
        }
    }

