import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';

// NgZorro
// import { NzMessageModule } from 'ng-zorro-antd/message';
import { NZ_I18N, pt_BR } from 'ng-zorro-antd/i18n';

// Interceptors
import { AuthInterceptor } from './core/interceptors/auth.interceptor';

// Locale
import { registerLocaleData } from '@angular/common';
import pt from '@angular/common/locales/pt';
import { AppComponent } from './app.component';
registerLocaleData(pt);

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    HttpClientModule,
    // NzMessageModule
  ],
  providers: [
    { provide: NZ_I18N, useValue: pt_BR },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }