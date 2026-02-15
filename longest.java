class longest {
    public static void main(String[] args) {
        int[]a ={3,2,4,-2,4,1,1};
        int k=6;
        int sum=0;
        int len=0;
        int l=0;
        for(int i=0;i<=a.length;i++)
        {
            sum=0;
            for(int j=i;j<a.length;j++)
            {
                sum+=a[j];
                if(sum>=k)
                {
                    if(sum==k)
                    l=j-i+1;
                }
            }
            if(l>len)
                len=l;
        }

        System.out.print(len);
    }
}
