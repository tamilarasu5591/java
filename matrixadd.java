import java.util.Scanner;
class matrixadd{
    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        System.out.println("enter the row:");
        int m=in.nextInt();
        System.out.println("enter the column:");
        int n=in.nextInt();
        int i,j;
        int[][] a=new int[m][n];
        int[][] b=new int[n][m];
        int[][] c=new int[m][m];
        for(i=0;i<m;i++){
            for(j=0;j<n;j++){
                a[i][j]=in.nextInt();
            }
        }
        for(i=0;i<n;i++){
            for(j=0;j<m;j++){
                b[i][j]=in.nextInt();
            }
        }
        for(i=0;i<m;i++){
            for(j=0;j<m;j++){
                for(int k=0;k<n;k++){
                 c[i][j] = a[i][k] * b[k][j];
                }
            }
        }
        System.out.print("matric multiplication:" );
        for(i=0;i<m;i++){
            for(j=0;j<n;j++){
                System.out.print(c[i][j]+" ");
                
            }
            System.out.println();
        }
    }
}