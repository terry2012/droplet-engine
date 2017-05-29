package ch.ethz.blockadit.blockadit;

import java.math.BigDecimal;
import java.math.RoundingMode;

import ch.ethz.blockadit.R;
import ch.ethz.blokcaditapi.storage.chunkentries.Averagor;
import ch.ethz.blokcaditapi.storage.chunkentries.EntryProcessor;
import ch.ethz.blokcaditapi.storage.chunkentries.Sumator;

/*
 * Copyright (c) 2016, Institute for Pervasive Computing, ETH Zurich.
 * All rights reserved.
 *
 * Author:
 *       Lukas Burkhalter <lubu@student.ethz.ch>
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */

public enum Datatype {
    STEPS,
    CALORIES,
    DISTANCE,
    FLOORS,
    HEARTRATE;

    public String getDisplayRep() {
        switch (this) {
            case HEARTRATE:
            case STEPS:
            case CALORIES:
            case DISTANCE:
            case FLOORS:
            default:
                return this.name();
        }

    }

    public static EntryProcessor getEntryProcessorForType(Datatype type) {
        switch (type) {
            case HEARTRATE:
                return new Averagor(1);
            case STEPS:
            case CALORIES:
            case DISTANCE:
            case FLOORS:
            default:
                return new Sumator(1);
        }
    }

    public static boolean filterPerType(Datatype type, String metadata) {
        return metadata.equals(type.getDisplayRep());
    }

    public static int performAVG(Datatype type, int num, int max) {
        switch (type) {
            case HEARTRATE:
                BigDecimal a = BigDecimal.valueOf(num);
                BigDecimal b = BigDecimal.valueOf(max);
                a = a.divide(b, RoundingMode.HALF_UP);
                return a.intValue();
            case STEPS:
            case CALORIES:
            case DISTANCE:
            case FLOORS:
            default:
                return num;
        }
    }

    public int getImgResource() {
        switch (this) {
            case STEPS:
                return R.drawable.step;
            case CALORIES:
                return R.drawable.calories;
            case DISTANCE:
                return R.drawable.distance;
            case FLOORS:
                return R.drawable.floor;
            case HEARTRATE:
                return R.drawable.hrb;
        }
        return R.drawable.login;
    }

    public String formatValue(double value) {
        switch (this) {
            case CALORIES:
                return String.format("%.0f", value);
            case DISTANCE:
                return String.format("%.2f", value);
            case HEARTRATE:
                return String.format("%.2f", value);
            case STEPS:
            case FLOORS:
            default:
                return String.valueOf((int) value);
        }
    }

    public String getUnit() {
        switch (this) {
            case CALORIES:
                return "calories";
            case DISTANCE:
                return "km";
            case STEPS:
                return "steps";
            case FLOORS:
                return "floors";
            case HEARTRATE:
                return "bpm";
            default:
                return "";
        }
    }

}
