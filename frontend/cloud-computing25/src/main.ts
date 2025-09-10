import { platformBrowser } from '@angular/platform-browser';
import { AppModule } from './app/app.module';
import { Amplify } from 'aws-amplify';

platformBrowser().bootstrapModule(AppModule, {
  ngZoneEventCoalescing: true,
})
  .catch(err => console.error(err));

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: 'eu-north-1_iEH9Htkfr',
      userPoolClientId: 'peenc0kbbl2ab010di3boavf8',
    },
  },
});
