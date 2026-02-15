class array {
    public static void main(String[] args) {
        int[] a = { 12, 10, 14, 1, 6 };
        for (int i = 0; i < a.length; i++) {
            boolean flag = true;
            for (int j = i + 1; j < a.length; j++) {
                if (a[i] > a[j]) {
                    flag = false;

                } else {
                    flag = true;
                    break;
                }
            }

            if (flag) {
                System.out.println(a[i] + " is not a leader");
            } else {
                System.out.println(a[i] + " is a leader");
            }
        }
    }
}
