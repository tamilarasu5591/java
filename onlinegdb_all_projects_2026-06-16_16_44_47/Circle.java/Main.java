/******************************************************************************

                            Online Java Compiler.
                Code, Compile, Run and Debug java program online.
Write your code in this editor and press "Run" button to execute it.

*******************************************************************************/

abstract class shape{
    int area;
    abstract public void calc();
}

class circle extends shape{
    int r;

    circle(int r){
        this.r = r;
    }

    public void calc(){
        area = (int)(3.14 * r * r);
        System.out.println("Area = " + area);
    }
}

class Main{
    public static void main(String[] args){
        circle c = new circle(5);
        c.calc();
    }
}

