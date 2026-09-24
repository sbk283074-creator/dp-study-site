public class Sol4 {
    static String clock(int totalSeconds) {
        int hours = totalSeconds / 3600;
        int minutes = totalSeconds % 3600 / 60;
        int seconds = totalSeconds % 60;
        return String.format("%d:%02d:%02d", hours, minutes, seconds);
    }

    public static void main(String[] args) {
        int[] samples = {0, 59, 60, 3599, 3600, 86_399, 100_000};
        boolean fieldsInRange = true;
        for (int sample : samples) {
            String rendered = clock(sample);
            System.out.println(sample + " seconds -> " + rendered);
            String[] parts = rendered.split(":");
            fieldsInRange = fieldsInRange
                    && Integer.parseInt(parts[1]) < 60
                    && Integer.parseInt(parts[2]) < 60;
        }
        System.out.println("minutes and seconds are always under 60: " + fieldsInRange);
        System.out.println("the last sample is 27 hours and 40 seconds: " + clock(100_000));
    }
}
