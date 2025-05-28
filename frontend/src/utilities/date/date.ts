// istanbul ignore file

const defaultOptions: Intl.DateTimeFormatOptions = {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
};

interface IFormatDateProps {
    date: Date;
    options?: Intl.DateTimeFormatOptions;
    locale?: string;
    resetDefaultProps?: boolean;
}

export const formatDate = ({ date, options = {}, locale, resetDefaultProps }: IFormatDateProps): string => {
    const dateTimeFormatOptions = resetDefaultProps ? { ...options } : { ...defaultOptions, ...options };
    return new Intl.DateTimeFormat(locale || 'en-US', dateTimeFormatOptions).format(date);
};
