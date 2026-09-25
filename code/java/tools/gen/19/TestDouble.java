import java.util.ArrayList;
import java.util.List;

public class TestDouble {
    interface Clock {
        int hour();
    }

    static class RealClock implements Clock {
        @Override
        public int hour() {
            return 9;
        }
    }

    static class FakeClock implements Clock {
        private final int hour;

        FakeClock(int hour) {
            this.hour = hour;
        }

        @Override
        public int hour() {
            return hour;
        }
    }

    static String greeting(Clock clock) {
        int hour = clock.hour();
        if (hour < 12) {
            return "Good morning";
        }
        return hour < 18 ? "Good afternoon" : "Good evening";
    }

    public static void main(String[] args) {
        List<String> seen = new ArrayList<>();
        for (int hour : new int[] {6, 13, 21}) {
            seen.add(greeting(new FakeClock(hour)));
        }
        System.out.println("fake = " + seen);
        System.out.println("real = " + greeting(new RealClock()));
    }
}
