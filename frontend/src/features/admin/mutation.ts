export async function runAdminMutation(
  action: () => Promise<void>,
  onError: (message: string) => void,
): Promise<boolean> {
  try {
    await action();
    return true;
  } catch (reason) {
    onError(reason instanceof Error ? reason.message : "Unable to update administration data.");
    return false;
  }
}
