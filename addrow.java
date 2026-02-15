import java.util.Scanner;
class main{
    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        int i;
        int sum=0;
        System.out.println("enter rows:" );
        int a=in.nextInt();
        System.out.println("enter columns:" );
        int b=in.nextInt();
        int[][] c=new int[a][b];
        for(i=0;i<a;i++){
        for(int j=0;j<b;j++){
            c[i][j]=in.nextInt();
        }
    }
    for(i=0;i<a;i++){
        for(int j=0;j<b;j++){
            sum=sum+c[i][j];
        }
        System.out.println(sum);
    }
}
}