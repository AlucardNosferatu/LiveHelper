package com.example.livehelper;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.TextView;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Locale;

import static java.lang.Thread.sleep;

public class MotionActivity extends AppCompatActivity implements SensorEventListener {
    ServerSocket SS=null;
    Socket S=null;
    OutputStream O=null;
    BufferedWriter BW=null;
    Boolean isListening=false;
    Boolean isSending=false;
    private TextView ACC;
    private SensorManager SM;
    private float[] gravity = new float[3];
    private String ACC_VALUE;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_motion);
        ACC = findViewById(R.id.ACC);
        SM =(SensorManager)getSystemService(Context.SENSOR_SERVICE);
        //注册加速度传感器
        SM.registerListener(this,SM.getDefaultSensor(Sensor.TYPE_ACCELEROMETER),SensorManager.SENSOR_DELAY_UI);//采集频率
        //注册重力传感器
        SM.registerListener(this,SM.getDefaultSensor(Sensor.TYPE_GRAVITY),SensorManager.SENSOR_DELAY_FASTEST);
        isListening=false;
        isSending=false;
    }
    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        //实现接口必须重写所有方法，不想写也得留空
    }

    public void SSwitch(View view){
        if(isListening)
        {

            isListening=false;
        }
        else
        {
            

            isListening=true;
        }
    }

    public void DSwitch(View view){
        if(isListening)
        {
            if(isSending)
            {

                isSending=false;
            }
            else
            {

                isSending=true;
            }

        }
        else
        {
            isSending=false;
            System.out.println("Do nothing.\n");
        }
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        //判断传感器类别
        switch (event.sensor.getType()) {
            case Sensor.TYPE_ACCELEROMETER: //加速度传感器
                final float alpha = (float) 0.8;
                gravity[0] = alpha * gravity[0] + (1 - alpha) * event.values[0];
                gravity[1] = alpha * gravity[1] + (1 - alpha) * event.values[1];
                gravity[2] = alpha * gravity[2] + (1 - alpha) * event.values[2];
                float VX = event.values[0] - gravity[0];
                float VY = event.values[1] - gravity[1];
                float VZ = event.values[2] - gravity[2];
                String VXS=String.format(Locale.CHINA,"%.2f", VX);
                String VYS=String.format(Locale.CHINA,"%.2f", VY);
                String VZS=String.format(Locale.CHINA,"%.2f", VZ);
                ACC_VALUE
                        = VXS + "#"
                        + VYS + "#"
                        + VZS;

                if(isListening)
                {
                    ACC.setText(ACC_VALUE);
                }
                //重力加速度9.81m/s^2，只受到重力作用的情况下，自由下落的加速度
                break;
            case Sensor.TYPE_GRAVITY://重力传感器
                gravity[0] = event.values[0];//单位m/s^2
                gravity[1] = event.values[1];
                gravity[2] = event.values[2];
                break;
            default:
                break;
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
    }

    @Override
    protected void onPause() {
        super.onPause();
    }

}

