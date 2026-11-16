import {afterEach,it,expect,vi} from 'vitest';
import type {ComponentProps} from 'react';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {PasswordChangeForm} from '../src/features/identity/password-change-form';
import {ValidationScope} from '../src/features/identity/field-validation';
afterEach(cleanup);
function view(onSubmit: ComponentProps<typeof PasswordChangeForm>['onSubmit']) {
 return <ValidationScope><PasswordChangeForm disabled={false} onSubmit={onSubmit}/></ValidationScope>;
}
function fill(confirm:string){fireEvent.change(screen.getByLabelText('Текущий пароль'),{target:{value:'synthetic current phrase'}});fireEvent.change(screen.getByLabelText('Новый пароль'),{target:{value:'synthetic new phrase'}});fireEvent.change(screen.getByLabelText('Повторите новый пароль'),{target:{value:confirm}});}
it('forwards matching passwords to the existing handler',()=>{const send=vi.fn(e=>e.preventDefault());render(view(send));fill('synthetic new phrase');fireEvent.click(screen.getByText('Сменить пароль'));expect(send).toHaveBeenCalledTimes(1);expect(screen.queryByRole('alert')).toBeNull();expect(screen.getByLabelText('Повторите новый пароль').getAttribute('autocomplete')).toBe('new-password');});
it('shows an associated mismatch error and sends nothing',()=>{const send=vi.fn();render(view(send));fill('different synthetic phrase');fireEvent.click(screen.getByText('Сменить пароль'));expect(send).not.toHaveBeenCalled();expect(screen.getByRole('alert').textContent).toContain('Пароли не совпадают');expect(screen.getByLabelText('Повторите новый пароль').getAttribute('aria-invalid')).toBe('true');});
