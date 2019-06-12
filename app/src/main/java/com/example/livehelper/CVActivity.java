package com.example.livehelper;

import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.provider.DocumentsContract;
import android.provider.MediaStore;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;

import org.opencv.android.BaseLoaderCallback;
import org.opencv.android.Utils;
import org.opencv.core.Mat;



public class CVActivity extends AppCompatActivity {
    private static final int RC_CHOOSE_PHOTO = 4;
    private static final String TAG = "CVActivity";
    private BaseLoaderCallback mLoaderCallback = new BaseLoaderCallback(this) {
        @Override
        public void onManagerConnected(int status){
            switch(status){
                case BaseLoaderCallback.SUCCESS:
                    Log.i(TAG,"成功加载");
                    break;
                default:
                    super.onManagerConnected(status);
                    Log.i(TAG,"加载失败");
                    break;
            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_cv);

    }

    public void ValueExtract(){


    }
    public void choosePic(View view){
        Intent GetImageIntent=new Intent(Intent.ACTION_GET_CONTENT);
        GetImageIntent.setType("image/*");
        startActivityForResult(GetImageIntent,RC_CHOOSE_PHOTO);
    }

    @Override
    protected void onActivityResult(int requestCode,int resultCode,Intent data){
        if(resultCode==RESULT_OK){

            Uri FileURI = data.getData();
            String WholeID=DocumentsContract.getDocumentId(FileURI);
            String ID=WholeID.split(":")[1];
            String FilePath="";

            String[] column = { MediaStore.Images.Media.DATA };
            String sel = MediaStore.Images.Media._ID + "=?";
            Cursor cursor = this.getContentResolver().query(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, column,sel, new String[] { ID }, null);
            int columnIndex = cursor.getColumnIndex(column[0]);
            if (cursor.moveToFirst()) {
                FilePath = cursor.getString(columnIndex);
            }
            cursor.close();
            Bitmap B=BitmapFactory.decodeFile(FilePath);
            
            ImageView IV=findViewById(R.id.imageView);
            IV.setImageBitmap(B);
        }
    }


}
