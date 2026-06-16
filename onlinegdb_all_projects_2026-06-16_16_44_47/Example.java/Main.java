/******************************************************************************

Welcome to GDB Online.
  GDB online is an online compiler and debugger tool for C, C++, Python, PHP, Ruby, 
  C#, OCaml, VB, Perl, Swift, Prolog, Javascript, Pascal, COBOL, HTML, CSS, JS
  Code, Compile, Run and Debug online from anywhere in world.

*******************************************************************************/
class Example{
    static int count;
    static{
        count=0;
        System.out.println("Static members initialized");
    }
    Example()
    {
        count=count+1;
    }
    static void disp()
    {
        System.out.print("count="+count);
    }
}
class Main{
    public static void main(String[] args){
        System.out.print("driver class started!");
        Example obj1=new Example();
        Example obj2=new Example();
        Example.disp();
    }
}