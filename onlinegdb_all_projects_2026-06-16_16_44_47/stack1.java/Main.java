/******************************************************************************

                            Online Java Compiler.
                Code, Compile, Run and Debug java program online.
Write your code in this editor and press "Run" button to execute it.

*******************************************************************************/

import java.util.Scanner;
import java.util.Stack;
public class Main {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        int n = in.nextInt();
        Stack<Integer> q1 = new Stack<>();
        for(int i = 0; i < n; i++) {
            q1.push(in.nextInt());
        }
        while(!q1.isEmpty()) {
            System.out.print(q1.pop() + " ");
        }
    }
}