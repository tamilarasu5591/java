import java.util.Scanner;
class binary{
    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        int value;
        String bin;
        String oct=" ";
        System.out.println("enter number:" );
        bin = in . next();
        while(bin.length()%3!=0)
        {
            bin="0"+bin;
        }
        for(int i=0; i<bin.length(); i=i+3)
        {
            value=0;
            value+=(bin.charAt(i)-'0')*4;
            value+=(bin.charAt(i+1)-'0')*2;
            value+=(bin.charAt(i+2)-'0')*1;
            oct=oct+value;
        }
        System.out.println(oct);
    }
}


