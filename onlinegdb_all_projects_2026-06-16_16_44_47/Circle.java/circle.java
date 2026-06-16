/******************************************************************************

                            Online Java Compiler.
                Code, Compile, Run and Debug java program online.
Write your code in this editor and press "Run" button to execute it.

*******************************************************************************/
interface Circle{
    double PI = 3.14;
    public void calc();
}
class arca implements Circle{
    double r, area;
    arca(double r)   
    {
        this.r = r;   
    }
    public void calc()
    {
        area = PI * r * r;
        System.out.println("Area = " + area);
    }
    public static void main(String[] s)
    {
        arca obj = new arca(10);  
        obj.calc();
    }
}
