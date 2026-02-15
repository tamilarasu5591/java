import java.util.Scanner;
class taamil{
    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        int a,b;
        String s1 = in.nextLine();
        String s2 = in.nextLine();
        int n1 = s1.length()-1;
        int n2 = s2.length()-1;
        while(n1>0|| n2>=0 || carry==1;
            {
                num=0;
                if(n1>0&&n2>0)
                    num=(s1.charAt(na)-'o')+(s2.charAt(n2)-'o')+carry;
                else if(n1>0)
                    num=(s1.charAt(n1)-'o')+carry;
                else if(n2>0)
                    num=(s2.charAt(n2)-'o')+carry;
                elsenum=carry;
                carry=num/2;
                num=num%2;
                sum=num+sum;
                n1--;
                n2--;
            }
        )
    }
}