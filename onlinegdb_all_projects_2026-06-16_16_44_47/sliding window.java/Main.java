/******************************************************************************

                            Online Java Compiler.
                Code, Compile, Run and Debug java program online.
Write your code in this editor and press "Run" button to execute it.

*******************************************************************************/
class main{
    public static void main(String[] args){
        int [] arr={2,1,5,3,2};
        int k=3;
        int sum=0;
        for(int i=0;i<k;i++){
            sum+=arr[i];
        }
        int maxsum=sum;
        for(int i=k;i<arr.length;i++){
            sum=sum-arr[i-k]+arr[i];
            int maxSum = Math.max(maxsum,sum);
        }
        System.out.println("Maximum Sum="+maxsum);
    }
}