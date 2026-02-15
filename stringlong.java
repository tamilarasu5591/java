
class stringlong {
    public static void main(String[] args) {
        Long s1 = 1234512345l;
        Long s2 = 1357912345l;

        while (s2 != 0) {
            long carry = s1 & s2;   // 
            s1 = s1 ^ s2;            
            s2 = carry << 1;       
        }

        System.out.println("Sum = " + s1);
    }
}  