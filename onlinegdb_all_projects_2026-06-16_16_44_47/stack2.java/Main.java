/******************************************************************************

Welcome to GDB Online.
  GDB online is an online compiler and debugger tool for C, C++, Python, PHP, Ruby, 
  C#, OCaml, VB, Perl, Swift, Prolog, Javascript, Pascal, COBOL, HTML, CSS, JS
  Code, Compile, Run and Debug online from anywhere in world.

*******************************************************************************/
import java.util.Scanner;
import java.util.Stack;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        Stack<Integer> history = new Stack<>();
        for(int i = 0; i < n; i++) {
            history.push(sc.nextInt());
        }
        if(history.size() <= 1) {
            System.out.println("No Previous Page");
        } else {
            history.pop(); 
            System.out.println(history.peek()); 
        }
    }
}