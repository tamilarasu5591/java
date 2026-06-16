/******************************************************************************

                            Online Java Compiler.
                Code, Compile, Run and Debug java program online.
Write your code in this editor and press "Run" button to execute it.

*******************************************************************************/
import java.util.Scanner;

class PostfixEvaluation
{
    int stack[] = new int[20];
    int top = -1;

    void push(int data)
    {
        top++;
        stack[top] = data;
    }

    int pop()
    {
        int val = stack[top];
        top--;
        return val;
    }

    public static void main(String args[])
    {
        PostfixEvaluation obj = new PostfixEvaluation();
        Scanner sc = new Scanner(System.in);

        System.out.println("Enter Postfix Expression:");
        String exp = sc.next();

        for(int i = 0; i < exp.length(); i++)
        {
            char ch = exp.charAt(i);

            if(ch >= '0' && ch <= '9')
            {
                obj.push(ch - '0');
            }
            else
            {
                int b = obj.pop();
                int a = obj.pop();

                switch(ch)
                {
                    case '+':
                        obj.push(a + b);
                        break;

                    case '-':
                        obj.push(a - b);
                        break;

                    case '*':
                        obj.push(a * b);
                        break;

                    case '/':
                        obj.push(a / b);
                        break;
                }
            }
        }

        System.out.println("Result = " + obj.pop());
    }
}