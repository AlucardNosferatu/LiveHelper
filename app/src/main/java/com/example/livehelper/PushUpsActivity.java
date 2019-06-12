package com.example.livehelper;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

public class PushUpsActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_push_ups);
    }
    public void increasePUC(View view){
        TextView tv=findViewById(R.id.PUCounts);
        String counts=tv.getText().toString();
        int countsInt = Integer.parseInt(counts);
        countsInt++;
        tv.setText(countsInt+"");
    }
}
