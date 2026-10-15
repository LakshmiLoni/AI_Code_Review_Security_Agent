
public class Main {
    public static int calculateTotal(int price, int quantity) {
        return price * quantity;
    }

    public static void main(String[] args) {
        int result = calculateTotal(100, 3);
        System.out.println("Total: " + result);
    }
}
