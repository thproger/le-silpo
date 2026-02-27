import { Routes } from '@angular/router';
import { ImportCsv } from './components/import-csv/import-csv';
import { OrdersList } from './components/orders-list/orders-list';
import { ManualCreate } from './components/manual-create/manual-create';

export const routes: Routes = [
    { path: '', redirectTo: 'import', pathMatch: 'full' }, // за замовчуванням
    { path: 'import', component: ImportCsv },
    { path: 'list', component: OrdersList },
    { path: 'manual', component: ManualCreate },
];