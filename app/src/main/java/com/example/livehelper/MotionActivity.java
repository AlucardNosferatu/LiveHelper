package com.example.livehelper;

import android.content.Context;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.hardware.SensorEventListener;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

import lecho.lib.hellocharts.model.Line;
import lecho.lib.hellocharts.model.LineChartData;
import lecho.lib.hellocharts.model.PointValue;
import lecho.lib.hellocharts.view.LineChartView;

public class MotionActivity extends AppCompatActivity implements SensorEventListener {
    private Boolean isRecord;
    private TextView ACC;
    private SensorManager SM;
    private float[] gravity = new float[3];
    private List<PointValue> dataX;
    private List<PointValue> dataY;
    private List<PointValue> dataZ;
    LineChartView lineChart;
    LineChartData LCD;
    List<Line> Lines;
    int counts;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_motion);
        isRecord=false;
        dataX=new ArrayList<PointValue>();
        dataY=new ArrayList<PointValue>();
        dataZ=new ArrayList<PointValue>();
        lineChart=(LineChartView)findViewById(R.id.line_chart);
        LCD=new LineChartData();
        Lines=new ArrayList<Line>();
        LCD.setLines(Lines);
        counts=0;
        ACC = (TextView) findViewById(R.id.ACC);
        SM =(SensorManager)getSystemService(Context.SENSOR_SERVICE);
    }
    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        //实现接口必须重写所有方法，不想写也得留空
    }

    public void MonitorSwitch(View view){
        if(isRecord) {
            isRecord = false;
        }
        else{
            dataX.clear();
            dataY.clear();
            dataZ.clear();
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
                String ACC_VALUE
                        = "x:" + VX + "\t"
                        + "y:" + VY + "\t"
                        + "z:" + VZ;
                if(isRecord){
                    if(counts<10){
                        counts++;
                    }
                    else{
                        Lines.clear();
                        counts=0;
                        dataX.add(new PointValue(VX,dataX.size()));
                        dataY.add(new PointValue(VY,dataY.size()));
                        dataZ.add(new PointValue(VZ,dataZ.size()));
                        Line LX = new Line(dataX);
                        Line LY = new Line(dataY);
                        Line LZ = new Line(dataZ);
                        LX.setColor(Color.parseColor("#0000FF"));
                        LY.setColor(Color.parseColor("#00FF00"));
                        LZ.setColor(Color.parseColor("#FF0000"));
                        Lines.add(LX);
                        Lines.add(LY);
                        Lines.add(LZ);
                        lineChart.setLineChartData(LCD);
                        if(dataX.size()>=20){
                            isRecord=false;
                        }
                    }
                }
                ACC.setText(ACC_VALUE);

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

    protected void onResume() {
        super.onResume();
        //注册加速度传感器
        SM.registerListener((SensorEventListener) this,SM.getDefaultSensor(Sensor.TYPE_ACCELEROMETER),SensorManager.SENSOR_DELAY_UI);//采集频率
        //注册重力传感器
        SM.registerListener((SensorEventListener) this,SM.getDefaultSensor(Sensor.TYPE_GRAVITY),SensorManager.SENSOR_DELAY_FASTEST);
    }

    @Override
    protected void onPause() {
        super.onPause();
        SM.unregisterListener((SensorEventListener) this);
    }

}
