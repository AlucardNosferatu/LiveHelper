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

    private Boolean isRecord;
    private TextView ACC;
    private SensorManager SM;
    private float[] gravity = new float[3];

    int counts;
    String ACC_VALUE;
    int PortNo;
    TextView PortNoText;
    Thread thread;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_motion);
        isRecord=false;
        counts=0;
        ACC = findViewById(R.id.ACC);
        SM =(SensorManager)getSystemService(Context.SENSOR_SERVICE);

        //注册加速度传感器
        SM.registerListener(this,SM.getDefaultSensor(Sensor.TYPE_ACCELEROMETER),SensorManager.SENSOR_DELAY_UI);//采集频率
        //注册重力传感器
        SM.registerListener(this,SM.getDefaultSensor(Sensor.TYPE_GRAVITY),SensorManager.SENSOR_DELAY_FASTEST);

        PortNoText=findViewById(R.id.editPort);
        MyThread myThread = new MyThread();
        this.thread = new Thread(myThread);
    }
    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        //实现接口必须重写所有方法，不想写也得留空
    }

    public void MonitorSwitch(View view){
        if(isRecord) {
            isRecord = false;
            try{
                SS.close();
                S.close();
                O.close();
                BW.close();
            }
            catch(IOException e)
            {
                e.printStackTrace();
            }
            if(this.thread.isAlive()){
                this.thread.interrupt();
                this.thread = null;
            }
        }
        else{
            if(this.thread.isAlive()){
                this.thread.interrupt();
                this.thread = null;
                MyThread myThread = new MyThread();
                this.thread = new Thread(myThread);
                this.thread.start();
            }
            else{
                this.thread.start();
            }
            isRecord = true;
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

                if(isRecord){
                    if(counts<2){
                        counts++;
                    }
                    else{
                        counts=0;
                    }
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


    class MyThread implements Runnable {
        @Override
        public void run() {
            FeedDicks();
        }
    }

    private void FeedDicks(){
        PortNo = Integer.parseInt(PortNoText.getText().toString());
        if(PortNo < 1024 || PortNo > 65535)
        {
            PortNo=54500;
        }
        try{
            SS = new ServerSocket(PortNo,32);
            //等待客户端的连接
            System.out.println("等待客户端连接！");
            S = SS.accept();
            System.out.println("与客户端连接成功！");
            //调用execute()方法时，如果必要，会创建一个新的线程来处理任务，但它首先会尝试使用已有的线程，
            //如果一个线程空闲60秒以上，则将其移除线程池；
            //另外，任务是在Executor的内部排队，而不是在网络中排队
            O = S.getOutputStream();
            BW = new BufferedWriter(new OutputStreamWriter(O));
            while(true){
                sleep(200);
                BW.write(ACC_VALUE);
                BW.flush();
            }
        }
        catch(Exception e){
            e.printStackTrace();
        }
    }

}

