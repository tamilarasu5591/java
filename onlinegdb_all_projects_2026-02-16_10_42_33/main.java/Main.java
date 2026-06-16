/******************************************************************************

                            Online Java Compiler.
                Code, Compile, Run and Debug java program online.
Write your code in this editor and press "Run" button to execute it.

*******************************************************************************/

class Main {
    public static void main(String[] args) {
        Long s1 = new Long("1234512345");
        Long s2 = new Long("1357912345");

        while (s2 != 0) {
            long carry = s1 & s2;   // 
            s1 = s1 ^ s2;            
            s2 = carry << 1;       
        }

        System.out.println("Sum = " + s1);
    }
}
