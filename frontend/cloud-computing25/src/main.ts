import { platformBrowser } from '@angular/platform-browser';
import { AppModule } from './app/app.module';
import { Amplify } from 'aws-amplify';
import {environment} from './env/environment';

platformBrowser().bootstrapModule(AppModule, {
  ngZoneEventCoalescing: true,
})
  .catch(err => console.error(err));

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: environment.userPoolId,
      userPoolClientId: environment.userPoolClientId,
    },
  },
});
