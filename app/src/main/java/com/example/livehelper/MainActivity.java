package com.example.livehelper;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;

// TODO: 2019/6/15 test GithubAPI and SensorManager 

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }
    public  void enterPU(View view){
        Intent intent = new Intent();
        intent.setClass(MainActivity.this,PushUpsActivity.class);
        startActivity(intent);
    }
    public  void enterCV(View view){
        Intent intent = new Intent();
        intent.setClass(MainActivity.this,CVActivity.class);
        startActivity(intent);
    }
    public  void enterNLP(View view){
        Intent intent = new Intent();
        intent.setClass(MainActivity.this,NLPActivity.class);
        startActivity(intent);
    }
}
