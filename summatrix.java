
class summatrix{
    public static void main(String[] args){
        int[][] r={{1,2,3,4,5},{1,2,3,4,5},{1,2,3}};
        int sum=0;
        for(int i=0;i<r.length;i++){                
            for(int j=0;j<r[i].length;j++){
                sum=sum+r[i][j];
            }
            }
            System.out.println(sum);
        }
    }