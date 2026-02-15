class strings{
    public static void main(String[] args){
        String s1="1234512345";
        String s2="1357912345";
        String result = addStrings(s1, s2);
        System.out.println(result);
    }
       Static String addStrings(string s1,String s2){
          StringBuilder result = new StringBuilder();
          int i = s1.length()-1;
          int j = s2.length()-1;
          int carry = 0;
          while(i>=0 || j>=0 || carry>0){
            int digit1 = i>=0 ? s1.charAt(i--) - '0' : 0;
            int digit2 = j>=0 ? s2.charAt(j--) - '0' : 0;
            int sum = digit1 + digit2 + carry;
            result.append(sum % 10);
            carry = sum / 10;
          }
          return result.reverse().toString();    
        }
    }