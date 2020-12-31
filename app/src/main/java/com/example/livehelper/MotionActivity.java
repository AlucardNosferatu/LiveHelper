package com.example.livehelper;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.CharBuffer;
import java.util.Locale;

import static java.lang.Thread.sleep;

public class MotionActivity extends AppCompatActivity implements SensorEventListener {
    ServerSocket SS=null;
    Socket S=null;
    OutputStream O=null;
    InputStream I=null;
    BufferedWriter BW=null;
    BufferedReader BR=null;
    Boolean isListening=false;
    private TextView ACC;
    private float[] gravity = new float[3];
    private String ACC_VALUE;
    private Thread TSend;
    private MyThread myThread;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_motion);
        ACC = findViewById(R.id.ACC);
        SensorManager SM = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        //注册加速度传感器
        SM.registerListener(this, SM.getDefaultSensor(Sensor.TYPE_ACCELEROMETER),SensorManager.SENSOR_DELAY_UI);//采集频率
        //注册重力传感器
        SM.registerListener(this, SM.getDefaultSensor(Sensor.TYPE_GRAVITY),SensorManager.SENSOR_DELAY_FASTEST);
        isListening=false;
        myThread = new MyThread();
    }
    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        //实现接口必须重写所有方法，不想写也得留空
    }

    class MyThread implements Runnable {
        @Override
        public void run() {
            ScanClient();
        }
    }

    private void ScanClient(){
        while(true)
        {
            if(isListening){
                try {
                    S = SS.accept();
                    I = S.getInputStream();
                    O = S.getOutputStream();
                    BR = new BufferedReader(new InputStreamReader(I));
                    BW = new BufferedWriter(new OutputStreamWriter(O));
                    while(true){
                        BW.write(ACC_VALUE+"\n");
                        BW.flush();
                        String GetStr=BR.readLine();
                        while(!GetStr.equals("recv"))
                        {
                            System.out.println(GetStr);
                            sleep(1);
                            GetStr=BR.readLine();
                        }
                    }
                }
                catch(Exception e){
                    e.printStackTrace();
                }
            }
        }
    }

    public void SSwitch(View view){
        if(isListening)
        {
            try{
                if(BW!=null){
                    TSend.interrupt();
                    BW.close();
                    BR.close();
                    O.close();
                    I.close();
                    S.close();
                }
                SS.close();
                isListening=false;
                Button B=findViewById(R.id.SocketSwitch);
                B.setText("Listen");
            }
            catch(IOException e)
            {
                e.printStackTrace();
            }
        }
        else
        {
            TextView PortNoText=findViewById(R.id.editPort);
            int PortNo=Integer.parseInt(PortNoText.getText().toString());
            try {
                SS = new ServerSocket(PortNo, 32);
                TSend = new Thread(myThread);
                TSend.start();
            }
            catch(IOException e)
            {
                e.printStackTrace();
            }
            isListening=true;
            Button B=findViewById(R.id.SocketSwitch);
            B.setText("Disconnect");
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

