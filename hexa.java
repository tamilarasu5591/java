import java.util.Scanner;
class hexa{
    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        String hex = " ";
        int dec;
        int rem;
        System.out.println("enter number:" );
        dec = in.nextInt();
        while(dec>16)
        {
            rem=dec%10;
            if(rem<10)
                hex=rem+hex;
            else if(rem<=16)
            {
                rem=(rem-8)+'A';

                hex=(char)rem+hex;   
                }
                dec=dec/16;
                
            }
             System.out.println(hex);
        }
       
    }
