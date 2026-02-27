import { Routes } from '@angular/router';
import { ImportCsv } from './import-csv/import-csv';
import { OrdersList } from './orders-list/orders-list';
import { ManualCreate } from './manual-create/manual-create';

export const routes: Routes = [
  { path: '', redirectTo: 'import', pathMatch: 'full' },
  { path: 'import', component: ImportCsv },
  { path: 'list', component: OrdersList },
  { path: 'manual', component: ManualCreate },
];
