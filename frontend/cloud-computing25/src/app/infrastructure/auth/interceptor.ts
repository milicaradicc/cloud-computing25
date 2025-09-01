import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable, from } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { fetchAuthSession } from 'aws-amplify/auth';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return from(fetchAuthSession()).pipe(
      switchMap(session => {
        const token = session.tokens?.idToken?.toString();
        const authReq = token
          ? req.clone({
            setHeaders: {
              Authorization: `Bearer ${token}`,
            },
          })
          : req;
        return next.handle(authReq);
      })
    );
  }
}

