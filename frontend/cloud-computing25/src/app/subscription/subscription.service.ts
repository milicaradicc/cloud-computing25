import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../env/environment';
import {HttpClient} from '@angular/common/http';
import { Subscription } from './subscription.model';
import { CreateSubscriptionDto } from './create-subscription-dto.model';

@Injectable({
  providedIn: 'root'
})
export class SubscriptionService {

  constructor(private httpClient: HttpClient) { }

  getSubscriptionsByUser(userId:string): Observable<Subscription[]> {
    return this.httpClient.get<Subscription[]>(`${environment.apiHost}/subscriptions?userId=${userId}`);
  }

  add(subscription: CreateSubscriptionDto): Observable<Subscription> {
    console.log(subscription);
    return this.httpClient.post<Subscription>(`${environment.apiHost}/subscriptions`, subscription);
  }

  delete(subscription: Subscription): Observable<any> {
    return this.httpClient.delete(`${environment.apiHost}/subscriptions/`+subscription.id);
  }
}

