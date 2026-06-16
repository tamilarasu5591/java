/******************************************************************************

                            Online Java Compiler.
                Code, Compile, Run and Debug java program online.
Write your code in this editor and press "Run" button to execute it.

*******************************************************************************/
import java.util.Scanner;

class A {
    int a;
    A() {
        a = 0;
    }
    public void get() {
        Scanner in = new Scanner(System.in);
        a = in.nextInt();
    }
}
class B extends A {
    int b;
    B() {
        super();
        b = 0;
    }
    public void get() {
        super.get();
        Scanner in = new Scanner(System.in);
        b = in.nextInt();
    }
    public static void main(String[] s) {
        B obj = new B();
        obj.get();
    }
}