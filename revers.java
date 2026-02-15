
class revers{
    public static void main(String[] args) {

        int[] a = {1,2,3,4,5};
        int k=2;
        for(int j=0;j<k;j++){
        int first_element=a[0];
        for (int i = 0; i < a.length-1; i++) {
            a[i]=a[i+1];
        }
        a[a.length-1]=first_element;
        
    }
    for(int i=0;i<a.length;i++)
        {
            System.out.println(a[i]);
        }
        }
    }

