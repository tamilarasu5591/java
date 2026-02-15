class array23{
    public static void main(String[] args)
    {
        int[] n ={1,2,3,4};
        int i;
        int a=2;
        int product=1;
        for( i=0;i<=n.length;i++){
                if(a==i){
                    continue;
                }
                else{
                    product*=n[i];
                }
            }
            System.out.println(product);
            }
        }
    